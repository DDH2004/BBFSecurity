import pexpect
import re
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parent.parent / "midnight-examples-0.2.2" / "examples" / "counter" / "counter-cli"

def log_access(wallet_seed: str, contract_hex: str):
    """
    Fully automates Midnight CLI:
    - Builds wallet
    - Waits for sync
    - Joins contract
    - Increments counter
    - Exits
    """
    child = pexpect.spawn("yarn testnet-remote", cwd=str(CLI_DIR), encoding="utf-8")

    try:
        print("🔧 Building wallet from seed...")
        child.expect("Which would you like to do\\?")
        child.sendline("2")

        child.expect("Enter your wallet seed:")
        child.sendline(wallet_seed)

        print("📡 Syncing wallet...")

        # Watch all output until the final menu returns
        while True:
            line = child.readline()
            if not line:
                break
            print(line.strip())

            if "Your wallet address is:" in line:
                address = line.split("Your wallet address is:")[-1].strip()
                print(f"🚀 Wallet created: {address}")
                print("⏳ Waiting for you to send tokens...")

            if re.search(r"You can do one of the following:", line):
                # Grab next line to confirm it's the full prompt
                next_line = child.readline()
                if re.search(r"1\\.", next_line) or "1." in next_line:
                    print("✅ Wallet synced and ready.")
                    break
            if re.search(r"Which would you like to do\\?", line):
                break

        # Join existing contract
        print("🔗 Joining contract...")
        child.sendline("2")
        child.expect("What is the contract address \\(in hex\\)\\?")
        child.sendline(contract_hex)

        # Increment
        print("➕ Incrementing counter...")
        child.expect("Which would you like to do\\?")
        child.sendline("1")

        # Wait for prompt to return after increment
        print("🔁 Waiting for post-increment prompt...")
        child.expect([
            "Which would you like to do\\?",
            "You can do one of the following:"
        ], timeout=200)

        # Exit cleanly
        child.sendline("3")

        print("✅ CLI log successful.")

    except pexpect.exceptions.TIMEOUT:
        print("❌ CLI timed out while waiting for token sync.")
    except pexpect.exceptions.EOF:
        print("❌ CLI exited unexpectedly.")
    finally:
        child.close()
