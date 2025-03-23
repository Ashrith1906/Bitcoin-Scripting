import json
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from pprint import PrettyPrinter

# RPC Configuration
USER = "StandUp"
PASSWD = "6305f1b2dbb3bc5a16cd0f4aac7e1eba"
ADDRESS = "127.0.0.1"
PORT_NUM = "18332"
WALLET_NAME = "MyNewWallet"

class BTCController:
    def __init__(self):
        self.output = PrettyPrinter(indent=2)
        self.rpc_conn = None

    def _construct_endpoint(self, wallet=None):
        """Builds RPC endpoint URL."""
        base_url = f"http://{USER}:{PASSWD}@{ADDRESS}:{PORT_NUM}"
        return f"{base_url}/wallet/{wallet}" if wallet else base_url

    def _connect(self, wallet=None):
        """Establishes RPC connection."""
        return AuthServiceProxy(self._construct_endpoint(wallet))

    def _configure_wallet(self):
        """Sets up or loads the wallet."""
        rpc_base = self._connect()
        wallets_active = rpc_base.listwallets()

        if WALLET_NAME not in wallets_active:
            print(f"[INFO] Wallet '{WALLET_NAME}' not detected.")
            try:
                rpc_base.loadwallet(WALLET_NAME)
                print(f"[SUCCESS] Loaded wallet: {WALLET_NAME}")
            except JSONRPCException as e:
                if "Wallet file verification failed" in str(e):
                    print(f"[ACTION] Creating wallet '{WALLET_NAME}'...")
                    rpc_base.createwallet(WALLET_NAME)
                    print(f"[SUCCESS] Wallet '{WALLET_NAME}' created")
                else:
                    raise e
        return self._connect(WALLET_NAME)

    def generate_legacy_addr(self):
        """Creates a new Legacy address."""
        return self.rpc_conn.getnewaddress("", "legacy")

    def create_blocks(self, num, dest_addr):
        """Mines blocks to an address."""
        self.rpc_conn.generatetoaddress(num, dest_addr)

    def send_coins(self, target, qty):
        """Sends BTC and mines a block."""
        tx_hash = self.rpc_conn.sendtoaddress(target, qty)
        print(f"[TX] Dispatched {tx_hash} | Mining block for confirmation...")
        self.create_blocks(1, self.generate_legacy_addr())
        return tx_hash

    def dissect_transaction(self, tx_hash, addr_to_find):
        """Breaks down a transaction."""
        try:
            tx_info = self.rpc_conn.gettransaction(tx_hash, True)
            tx_decoded = self.rpc_conn.decoderawtransaction(tx_info["hex"])
            print("\n[TRANSACTION BREAKDOWN]")
            self.output.pprint(tx_decoded)

            print("[SCRIPTPUBKEY SEARCH]")
            for vout_item in tx_decoded["vout"]:
                script_data = vout_item.get("scriptPubKey", {})
                if script_data.get("address") == addr_to_find:
                    print(f"[FOUND] {addr_to_find} -> ScriptPubKey: {script_data['hex']}")
                    return script_data["hex"]
            print(f"[NOT FOUND] Address {addr_to_find} missing in outputs")
            return None
        except JSONRPCException as e:
            print(f"[RPC ERROR] {e}")
            return None
        except Exception as e:
            print(f"[GENERAL ERROR] {e}")
            return None

    def perform_tasks(self):
        """Executes the workflow."""
        try:
            # Wallet setup
            self.rpc_conn = self._configure_wallet()
            print(f"[STATUS] Operating on wallet: {WALLET_NAME}")

            # Wallet info
            info = self.rpc_conn.getwalletinfo()
            print("\n[WALLET STATUS]")
            self.output.pprint(info)

            # Mine blocks
            print("[MINING] Generating 101 blocks...")
            self.create_blocks(101, self.generate_legacy_addr())

            # Generate addresses
            addr_a = self.generate_legacy_addr()
            addr_b = self.generate_legacy_addr()
            addr_c = self.generate_legacy_addr()
            print("[ADDRESSES]")
            print(f" - A: {addr_a}")
            print(f" - B: {addr_b}")
            print(f" - C: {addr_c}")

            # First transaction
            print("[TRANSFER] Sending 1 BTC from A to B")
            tx_id1 = self.send_coins(addr_b, 1.0)
            print(f"[TX ID] {tx_id1}")

            # Analyze transaction
            print("\n[ANALYSIS] Checking transaction for B's ScriptPubKey")
            script_pk = self.dissect_transaction(tx_id1, addr_b)

            # Second transaction
            print("[TRANSFER] Sending 0.5 BTC from B to C")
            tx_id2 = self.send_coins(addr_c, 0.5)
            print(f"[TX ID] {tx_id2}")

            # Balance
            bal = self.rpc_conn.getbalance()
            print(f"[BALANCE] Total: {bal} BTC")

        except JSONRPCException as e:
            print(f"[RPC FAILURE] {e}")
        except Exception as e:
            print(f"[TASK ERROR] {e}")

if __name__ == "__main__":
    controller = BTCController()
    controller.perform_tasks()