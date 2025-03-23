from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import pprint

# RPC Setup Constants
AUTH_USERNAME = "StandUp"
AUTH_PASSWORD = "6305f1b2dbb3bc5a16cd0f4aac7e1eba"
SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = "18332"
WALLET_LABEL = "MyNewWallet"

class BitcoinProcessor:
    def __init__(self):
        self.formatter = pprint.PrettyPrinter(indent=2)
        self.rpc_link = None

    def _link_to_rpc(self, wallet_label=None):
        """Sets up RPC connection."""
        uri = f"http://{AUTH_USERNAME}:{AUTH_PASSWORD}@{SERVER_ADDRESS}:{SERVER_PORT}"
        if wallet_label:
            uri += f"/wallet/{wallet_label}"
        return AuthServiceProxy(uri)

    def _prepare_wallet(self):
        """Ensures wallet is available."""
        temp_link = self._link_to_rpc()
        wallet_list = temp_link.listwallets()

        if WALLET_LABEL not in wallet_list:
            print(f"-> Notice: '{WALLET_LABEL}' not currently active.")
            try:
                temp_link.loadwallet(WALLET_LABEL)
                print(f"-> Success: '{WALLET_LABEL}' is now active.")
            except JSONRPCException as exc:
                if "Wallet file verification failed" in str(exc):
                    print(f"-> Info: '{WALLET_LABEL}' not found, initializing...")
                    temp_link.createwallet(WALLET_LABEL)
                    print(f"-> Done: '{WALLET_LABEL}' initialized.")
                else:
                    raise exc
        return self._link_to_rpc(WALLET_LABEL)

    def fetch_segwit(self):
        """Obtains a SegWit Bech32 address."""
        return self.rpc_link.getnewaddress("", "bech32")

    def produce_blocks(self, count):
        """Creates blocks for mining."""
        target = self.fetch_segwit()
        self.rpc_link.generatetoaddress(count, target)

    def dispatch_btc(self, receiver, qty):
        """Sends BTC and confirms it."""
        tx_ref = self.rpc_link.sendtoaddress(receiver, qty)
        print(f"-> Transaction Initiated: {tx_ref} | Confirming with block...")
        self.produce_blocks(1)
        return tx_ref

    def examine_tx(self, tx_ref, search_addr):
        """Inspects transaction details."""
        try:
            tx_raw = self.rpc_link.gettransaction(tx_ref, True)
            tx_struct = self.rpc_link.decoderawtransaction(tx_raw["hex"])
            print("\n=== Transaction Analysis ===")
            print("Details:")
            self.formatter.pprint(tx_struct)

            print("\n=== ScriptPubKey Search ===")
            for out in tx_struct["vout"]:
                script_info = out["scriptPubKey"]
                if script_info.get("address") == search_addr:
                    result = script_info["hex"]
                    print(f"-> Match Found: {search_addr} -> {result}")
                    return result
            print(f"-> No Match: {search_addr} not in outputs.")
            return None
        except JSONRPCException as exc:
            print(f"-> RPC Fault: {exc}")
            return None
        except Exception as exc:
            print(f"-> Error Encountered: {exc}")
            return None

    def execute_sequence(self):
        """Runs the full operation set."""
        try:
            # Wallet initialization
            self.rpc_link = self._prepare_wallet()
            print(f"-> Wallet Link Established: '{WALLET_LABEL}'")

            # Wallet summary
            summary = self.rpc_link.getwalletinfo()
            print("\n=== Wallet Summary ===")
            self.formatter.pprint(summary)

            # Block generation
            print("-> Starting Block Generation: 101 blocks")
            self.produce_blocks(101)

            # Address creation
            addr1 = self.fetch_segwit()
            addr2 = self.fetch_segwit()
            addr3 = self.fetch_segwit()
            print(f"-> Generated Addresses:")
            print(f"   1. {addr1}")
            print(f"   2. {addr2}")
            print(f"   3. {addr3}")

            # First transfer
            print("-> Initiating Transfer: 1 BTC from Addr1 to Addr2")
            tx_ref1 = self.dispatch_btc(addr2, 1.0)
            print(f"-> TX Reference: {tx_ref1}")

            # Transaction inspection
            print("\n-> Examining TX for Addr2 ScriptPubKey")
            script_result = self.examine_tx(tx_ref1, addr2)

            # Second transfer
            print("-> Initiating Transfer: 0.5 BTC from Addr2 to Addr3")
            tx_ref2 = self.dispatch_btc(addr3, 0.5)
            print(f"-> TX Reference: {tx_ref2}")

            # Balance check
            funds = self.rpc_link.getbalance()
            print(f"-> Current Funds: {funds} BTC")

        except JSONRPCException as exc:
            print(f"-> RPC Issue: {exc}")
        except Exception as exc:
            print(f"-> Sequence Failed: {exc}")

if __name__ == "__main__":
    processor = BitcoinProcessor()
    processor.execute_sequence()