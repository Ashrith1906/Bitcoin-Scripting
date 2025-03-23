# Bitcoin Scripting Assignment

## *Team Information*
*Team Name:* HASHFLOW  
*Team Members:*
- Kotha Ashrith Reddy  - 230001043
- Buditi Deepak   -   230001016
- Avvaru Venkata Sai Deepak   -   230001011
- Vivek Tej Kanakam   -   230041014


## *Project Overview*
This project demonstrates Bitcoin transactions using two address types:
- *Legacy Transactions (P2PKH)*
- *SegWit Transactions (P2SH-P2WPKH)*

The scripts execute Bitcoin transactions using Python and Bitcoin Core RPC, including wallet creation, mining, transaction execution, and validation.

---

## *Prerequisites*
Ensure the following software is installed:
- *Bitcoin Core* (Testnet/Regtest Mode)
- *Python 3*
- *Required Libraries:*
  
 `pip install python-bitcoinrpc`
  

### *Bitcoin Core Configuration*
Add the following lines to bitcoin.conf to enable RPC communication:

ini
server=1
testnet=1
txindex=1
rpcuser=StandUp
rpcpassword=6305f1b2dbb3bc5a16cd0f4aac7e1eba
rpcport=18332


Start Bitcoin Core in testnet mode:

`bitcoind -daemon -testnet`


---

## *Project Files*
- p2pkh.py - Implements *Legacy Transactions (P2PKH)*
- segwit.py - Implements *SegWit Transactions (P2SH-P2WPKH)*

---

## *How to Run the Scripts*
### *1. Run Legacy Transactions (P2PKH)*

`python p2pkh.py`

This script:
- Creates a wallet if not already existing.
- Generates *Legacy addresses*.
- Mines *101 blocks* for initial balance.
- Sends *1 BTC from Address A to B*.
- Decodes and extracts *ScriptPubKey*.
- Sends *0.5 BTC from B to C*.
- Checks final balance.

### *2. Run SegWit Transactions (P2SH-P2WPKH)*

`python segwit.py`

This script:
- Uses the same wallet.
- Generates *SegWit addresses*.
- Mines *101 additional blocks*.
- Sends *1 BTC from Address A' to B'*.
- Decodes and extracts *ScriptPubKey*.
- Sends *0.5 BTC from B' to C'*.
- Checks final balance.

---

## *Expected Output Format*
### *Legacy Transactions (P2PKH)*

[WALLET STATUS]  Wallet Balance: 12661.00000840 BTC  
[MINING]  Generating 101 blocks...  
[TRANSFER] Sending 1 BTC from A to B  
[TX]  Dispatched TXID: 79f86c...  
[ANALYSIS]  Checking transaction for B's ScriptPubKey  
[SCRIPTPUBKEY FOUND]  Address B -> ScriptPubKey: 76a914...  
[TRANSFER]  Sending 0.5 BTC from B to C  
[TX]  Dispatched TXID: 139ebf...  
[FINAL BALANCE]  12661.00000840 BTC

### *SegWit Transactions (P2SH-P2WPKH)*

[WALLET STATUS]  Wallet Balance: 13510.99998590 BTC  
[MINING]  Generating 101 blocks...  
[TRANSFER]  Sending 1 BTC from A' to B'  
[TX]  Dispatched TXID: bd2d61...  
[ANALYSIS]  Checking transaction for B's ScriptPubKey  
[SCRIPTPUBKEY FOUND]  Address B' -> ScriptPubKey: 0014...  
[TRANSFER]  Sending 0.5 BTC from B' to C'  
[TX]  Dispatched TXID: 5083bf...  
[FINAL BALANCE]  13510.99998590 BTC

---

## *Key Features of the Implementation*
### *1. Wallet Initialization*
Ensures that the wallet exists and loads it; otherwise, creates a new one.
python
def ensure_wallet():
    rpc_client = connect_rpc()
    if WALLET_NAME not in rpc_client.listwallets():
        rpc_client.createwallet(WALLET_NAME)
    return connect_rpc(WALLET_NAME)


### *2. Address Generation*
Creates *Legacy (P2PKH) and SegWit (P2SH-P2WPKH) addresses*.
python
def get_legacy_address(rpc_client):
    return rpc_client.getnewaddress("", "legacy")

def get_segwit_address(rpc_client):
    return rpc_client.getnewaddress("", "bech32")


### *3. Mining Blocks*
Generates blocks to receive Bitcoin testnet rewards.
python
def generate_blocks(rpc_client, num):
    miner_address = get_legacy_address(rpc_client)
    rpc_client.generatetoaddress(num, miner_address)


### *4. Sending Bitcoin Transactions*
Transfers Bitcoin from one address to another and mines a block for confirmation.
python
def send_bitcoins(rpc_client, to_address, amount):
    txid = rpc_client.sendtoaddress(to_address, amount)
    generate_blocks(rpc_client, 1)
    return txid


### *5. Transaction Decoding*
Extracts *ScriptPubKey* from transactions to verify the receiver’s address.
python
def decode_transaction(rpc_client, txid, target_address):
    raw_tx = rpc_client.gettransaction(txid, True)
    decoded_tx = rpc_client.decoderawtransaction(raw_tx['hex'])
    return [vout['scriptPubKey']['hex'] for vout in decoded_tx['vout'] if 'address' in vout['scriptPubKey'] and vout['scriptPubKey']['address'] == target_address]


---

## *Conclusion*
This project successfully implements and analyzes both *Legacy (P2PKH) and SegWit (P2SH-P2WPKH) transactions*, showcasing:
- *The efficiency of SegWit transactions* in reducing transaction size and fees.
- *The role of ScriptPubKey in transaction validation*.
- *The importance of SegWit in addressing transaction malleability* and enabling scaling solutions like the Lightning Network.

By working with Bitcoin Core RPC and scripting transactions in Python, we gain a practical understanding of Bitcoin's transaction structure and efficiency improvements in newer formats.

---

## *References*
- Bitcoin Core Documentation
- Learning Bitcoin from the Command Line (GitHub)
