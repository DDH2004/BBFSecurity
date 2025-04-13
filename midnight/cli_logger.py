import pexpect
import re
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parent.parent / "midnight-examples-0.2.2" / "examples" / "counter" / "counter-cli"

def log_access(wallet_seed: str, contract_hex: str):
    child = pexpect.spawn("yarn testnet-remote", cwd=str(CLI_DIR), encoding="utf-8")

    try:
        child.expect("Which would you like to do\\?", timeout=200)
        child.sendline("2")

        child.expect("Enter your wallet seed:", timeout=200)
        child.sendline(wallet_seed)

        # Wait for full wallet sync
        while True:
            line = child.readline()
            if not line:
                break
            print(line.strip())

            if "Your wallet address is:" in line:
                address = line.split("Your wallet address is:")[-1].strip()
                print(f"🚀 Wallet created: {address}")
                print("⏳ Waiting for tokens...")

            if re.search(r"You can do one of the following:", line):
                next_line = child.readline()
                if "1." in next_line:
                    print("✅ Wallet synced.")
                    break
            elif re.search(r"Which would you like to do\\?", line):
                break

        # Join contract
        child.sendline("2")
        child.expect("What is the contract address \\(in hex\\)\\?", timeout=200)
        child.sendline(contract_hex)

        # Increment
        child.expect("Which would you like to do\\?", timeout=200)
        child.sendline("1")

        # Wait for menu again
        child.expect([
            "Which would you like to do\\?",
            "You can do one of the following:"
        ], timeout=200)

        # Show counter value
        print("📊 Checking counter value...")
        child.sendline("2")

        child.expect("Current counter value:", timeout=200)
        value = child.readline().strip()
        print(f"🔢 Current value: {value}")

        # Exit
        child.expect("Which would you like to do\\?", timeout=200)
        child.sendline("3")

        print("✅ CLI log complete.")

    except pexpect.exceptions.TIMEOUT:
        print("❌ Timeout reached during CLI interaction.")
    except pexpect.exceptions.EOF:
        print("❌ CLI closed unexpectedly.")
    finally:
        child.close()


# --- add at bottom of midnight/cli_logger.py ------------------------
def get_counter_value(wallet_seed: str, contract_hex: str, timeout: int = 200) -> int:
    """
    Build wallet → join contract → display counter value → exit.
    Returns the integer counter value.
    """
    import pexpect, re
    child = pexpect.spawn("yarn testnet-remote",
                          cwd=str(CLI_DIR), encoding="utf-8")

    try:
        child.expect("Which would you like to do\\?", timeout=timeout)
        child.sendline("2")                       # build wallet from seed
        child.expect("Enter your wallet seed:", timeout=timeout)
        child.sendline(wallet_seed)

        # wait until wallet sync completes
        while True:
            line = child.readline()
            if not line:
                break
            if re.search(r"You can do one of the following:", line):
                child.readline(); break
            if re.search(r"Which would you like to do\\?", line):
                break

        child.sendline("2")                       # join contract
        child.expect("What is the contract address \\(in hex\\)\\?", timeout=timeout)
        child.sendline(contract_hex)

        child.expect("Which would you like to do\\?", timeout=timeout)
        child.sendline("2")                       # display counter value

        child.expect("Current counter value:", timeout=timeout)
        value_line = child.readline().strip()
        counter_val = int(value_line)

        child.expect("Which would you like to do\\?", timeout=timeout)
        child.sendline("3")                       # exit
        return counter_val

    finally:
        child.close()
# --------------------------------------------------------------------
