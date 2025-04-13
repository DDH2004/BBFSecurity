import { Counter, witnesses } from '@midnight-ntwrk/counter-contract';
import { nativeToken, Transaction } from '@midnight-ntwrk/ledger';
import { deployContract, findDeployedContract } from '@midnight-ntwrk/midnight-js-contracts';
import { httpClientProofProvider } from '@midnight-ntwrk/midnight-js-http-client-proof-provider';
import { indexerPublicDataProvider } from '@midnight-ntwrk/midnight-js-indexer-public-data-provider';
import { NodeZkConfigProvider } from '@midnight-ntwrk/midnight-js-node-zk-config-provider';
import { createBalancedTx, } from '@midnight-ntwrk/midnight-js-types';
import { WalletBuilder } from '@midnight-ntwrk/wallet';
import { Transaction as ZswapTransaction } from '@midnight-ntwrk/zswap';
import * as crypto from 'crypto';
import { webcrypto } from 'crypto';
import * as Rx from 'rxjs';
import { WebSocket } from 'ws';
import { contractConfig } from './config.js';
import { levelPrivateStateProvider } from '@midnight-ntwrk/midnight-js-level-private-state-provider';
import { assertIsContractAddress, toHex } from '@midnight-ntwrk/midnight-js-utils';
import { getLedgerNetworkId, getZswapNetworkId } from '@midnight-ntwrk/midnight-js-network-id';
import * as fsAsync from 'node:fs/promises';
import * as fs from 'node:fs';
let logger;
// @ts-expect-error: It's needed to make Scala.js and WASM code able to use cryptography
globalThis.crypto = webcrypto;
// @ts-expect-error: It's needed to enable WebSocket usage through apollo
globalThis.WebSocket = WebSocket;
export const getCounterLedgerState = async (providers, contractAddress) => {
    assertIsContractAddress(contractAddress);
    logger.info('Checking contract ledger state...');
    const state = await providers.publicDataProvider
        .queryContractState(contractAddress)
        .then((contractState) => (contractState != null ? Counter.ledger(contractState.data).round : null));
    logger.info(`Ledger state: ${state}`);
    return state;
};
export const counterContractInstance = new Counter.Contract(witnesses);
export const joinContract = async (providers, contractAddress) => {
    const counterContract = await findDeployedContract(providers, {
        contractAddress,
        contract: counterContractInstance,
        privateStateId: 'counterPrivateState',
        initialPrivateState: { privateCounter: 0 },
    });
    logger.info(`Joined contract at address: ${counterContract.deployTxData.public.contractAddress}`);
    return counterContract;
};
export const deploy = async (providers, privateState) => {
    logger.info('Deploying counter contract...');
    const counterContract = await deployContract(providers, {
        contract: counterContractInstance,
        privateStateId: 'counterPrivateState',
        initialPrivateState: privateState,
    });
    logger.info(`Deployed contract at address: ${counterContract.deployTxData.public.contractAddress}`);
    return counterContract;
};
export const increment = async (counterContract) => {
    logger.info('Incrementing...');
    const finalizedTxData = await counterContract.callTx.increment();
    logger.info(`Transaction ${finalizedTxData.public.txId} added in block ${finalizedTxData.public.blockHeight}`);
    return finalizedTxData.public;
};
export const displayCounterValue = async (providers, counterContract) => {
    const contractAddress = counterContract.deployTxData.public.contractAddress;
    const counterValue = await getCounterLedgerState(providers, contractAddress);
    if (counterValue === null) {
        logger.info(`There is no counter contract deployed at ${contractAddress}.`);
    }
    else {
        logger.info(`Current counter value: ${Number(counterValue)}`);
    }
    return { contractAddress, counterValue };
};
export const createWalletAndMidnightProvider = async (wallet) => {
    const state = await Rx.firstValueFrom(wallet.state());
    return {
        coinPublicKey: state.coinPublicKey,
        balanceTx(tx, newCoins) {
            return wallet
                .balanceTransaction(ZswapTransaction.deserialize(tx.serialize(getLedgerNetworkId()), getZswapNetworkId()), newCoins)
                .then((tx) => wallet.proveTransaction(tx))
                .then((zswapTx) => Transaction.deserialize(zswapTx.serialize(getZswapNetworkId()), getLedgerNetworkId()))
                .then(createBalancedTx);
        },
        submitTx(tx) {
            return wallet.submitTransaction(tx);
        },
    };
};
export const waitForSync = (wallet) => Rx.firstValueFrom(wallet.state().pipe(Rx.throttleTime(5_000), Rx.tap((state) => {
    const scanned = state.syncProgress?.synced ?? 0n;
    const total = state.syncProgress?.total.toString() ?? 'unknown number';
    const txs = state.transactionHistory.length;
    logger.info(`Wallet scanned ${scanned} indices out of ${total}, transactions=${txs}`);
}), Rx.filter((state) => {
    // Let's allow progress only if wallet is synced fully
    const synced = state.syncProgress?.synced ?? 0n;
    const total = state.syncProgress?.total ?? 50n;
    return state.syncProgress !== undefined && total === synced;
})));
export const waitForSyncProgress = async (wallet) => await Rx.firstValueFrom(wallet.state().pipe(Rx.throttleTime(5_000), Rx.tap((state) => {
    const scanned = state.syncProgress?.synced ?? 0n;
    const total = state.syncProgress?.total.toString() ?? 'unknown number';
    logger.info(`Wallet scanned ${scanned} indices out of ${total}`);
}), Rx.filter((state) => {
    // Let's allow progress only if syncProgress is defined
    return state.syncProgress !== undefined;
})));
export const waitForFunds = (wallet) => Rx.firstValueFrom(wallet.state().pipe(Rx.throttleTime(10_000), Rx.tap((state) => {
    const scanned = state.syncProgress?.synced ?? 0n;
    const total = state.syncProgress?.total.toString() ?? 'unknown number';
    logger.info(`Wallet processed ${scanned} indices out of ${total}, transactions=${state.transactionHistory.length}`);
}), Rx.filter((state) => {
    // Let's allow progress only if wallet is synced
    const synced = state.syncProgress?.synced;
    const total = state.syncProgress?.total;
    return synced !== undefined && synced === total;
}), Rx.map((s) => s.balances[nativeToken()] ?? 0n), Rx.filter((balance) => balance > 0n)));
export const buildWalletAndWaitForFunds = async ({ indexer, indexerWS, node, proofServer }, seed, filename) => {
    const directoryPath = process.env.SYNC_CACHE;
    let wallet;
    if (directoryPath !== undefined) {
        if (fs.existsSync(`${directoryPath}/${filename}`)) {
            logger.info(`Attempting to restore state from ${directoryPath}/${filename}`);
            try {
                const serializedStream = fs.createReadStream(`${directoryPath}/${filename}`, 'utf-8');
                const serialized = await streamToString(serializedStream);
                serializedStream.on('finish', () => {
                    serializedStream.close();
                });
                wallet = await WalletBuilder.restore(indexer, indexerWS, proofServer, node, serialized, 'info');
                wallet.start();
                const stateObject = JSON.parse(serialized);
                if ((await isAnotherChain(wallet, Number(stateObject.offset))) === true) {
                    logger.warn('The chain was reset, building wallet from scratch');
                    wallet = await WalletBuilder.buildFromSeed(indexer, indexerWS, proofServer, node, seed, getZswapNetworkId(), 'info');
                    wallet.start();
                }
                else {
                    const newState = await waitForSync(wallet);
                    // allow for situations when there's no new index in the network between runs
                    if ((newState.syncProgress?.total ?? 0n) >= stateObject.offset - 1) {
                        logger.info('Wallet was able to sync from restored state');
                    }
                    else {
                        logger.info(`Offset: ${stateObject.offset}`);
                        logger.info(`SyncProgress.total: ${newState.syncProgress?.total}`);
                        logger.warn('Wallet was not able to sync from restored state, building wallet from scratch');
                        wallet = await WalletBuilder.buildFromSeed(indexer, indexerWS, proofServer, node, seed, getZswapNetworkId(), 'info');
                        wallet.start();
                    }
                }
            }
            catch (error) {
                if (typeof error === 'string') {
                    logger.error(error);
                }
                else if (error instanceof Error) {
                    logger.error(error.message);
                }
                logger.warn('Wallet was not able to restore using the stored state, building wallet from scratch');
                wallet = await WalletBuilder.buildFromSeed(indexer, indexerWS, proofServer, node, seed, getZswapNetworkId(), 'info');
                wallet.start();
            }
        }
        else {
            logger.info('Wallet save file not found, building wallet from scratch');
            wallet = await WalletBuilder.buildFromSeed(indexer, indexerWS, proofServer, node, seed, getZswapNetworkId(), 'info');
            wallet.start();
        }
    }
    else {
        logger.info('File path for save file not found, building wallet from scratch');
        wallet = await WalletBuilder.buildFromSeed(indexer, indexerWS, proofServer, node, seed, getZswapNetworkId(), 'info');
        wallet.start();
    }
    const state = await Rx.firstValueFrom(wallet.state());
    logger.info(`Your wallet seed is: ${seed}`);
    logger.info(`Your wallet address is: ${state.address}`);
    let balance = state.balances[nativeToken()];
    if (balance === undefined || balance === 0n) {
        logger.info(`Your wallet balance is: 0`);
        logger.info(`Waiting to receive tokens...`);
        balance = await waitForFunds(wallet);
    }
    logger.info(`Your wallet balance is: ${balance}`);
    return wallet;
};
export const randomBytes = (length) => {
    const bytes = new Uint8Array(length);
    crypto.getRandomValues(bytes);
    return bytes;
};
export const buildFreshWallet = async (config) => await buildWalletAndWaitForFunds(config, toHex(randomBytes(32)), '');
export const configureProviders = async (wallet, config) => {
    const walletAndMidnightProvider = await createWalletAndMidnightProvider(wallet);
    return {
        privateStateProvider: levelPrivateStateProvider({
            privateStateStoreName: contractConfig.privateStateStoreName,
        }),
        publicDataProvider: indexerPublicDataProvider(config.indexer, config.indexerWS),
        zkConfigProvider: new NodeZkConfigProvider(contractConfig.zkConfigPath),
        proofProvider: httpClientProofProvider(config.proofServer),
        walletProvider: walletAndMidnightProvider,
        midnightProvider: walletAndMidnightProvider,
    };
};
export function setLogger(_logger) {
    logger = _logger;
}
export const streamToString = async (stream) => {
    const chunks = [];
    return await new Promise((resolve, reject) => {
        stream.on('data', (chunk) => {
            if (typeof chunk === 'string') {
                chunks.push(Buffer.from(chunk, 'utf8'));
            }
            else {
                chunks.push(Buffer.from(chunk));
            }
        });
        stream.on('error', (err) => {
            reject(err);
        });
        stream.on('end', () => {
            resolve(Buffer.concat(chunks).toString('utf8'));
        });
    });
};
export const isAnotherChain = async (wallet, offset) => {
    const state = await waitForSyncProgress(wallet);
    // allow for situations when there's no new index in the network between runs
    if (state.syncProgress !== undefined) {
        return state.syncProgress.total < offset - 1;
    }
};
export const saveState = async (wallet, filename) => {
    const directoryPath = process.env.SYNC_CACHE;
    if (directoryPath !== undefined) {
        logger.info(`Saving state in ${directoryPath}/${filename}`);
        try {
            await fsAsync.mkdir(directoryPath, { recursive: true });
            const serializedState = await wallet.serializeState();
            const writer = fs.createWriteStream(`${directoryPath}/${filename}`);
            writer.write(serializedState);
            writer.on('finish', function () {
                logger.info(`File '${directoryPath}/${filename}' written successfully.`);
            });
            writer.on('error', function (err) {
                logger.error(err);
            });
            writer.end();
        }
        catch (e) {
            if (typeof e === 'string') {
                logger.warn(e);
            }
            else if (e instanceof Error) {
                logger.warn(e.message);
            }
        }
    }
    else {
        logger.info('Not saving cache as sync cache was not defined');
    }
};
//# sourceMappingURL=api.js.map