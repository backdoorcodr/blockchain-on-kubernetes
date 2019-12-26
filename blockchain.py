import hashlib
import json
import logging
import requests

from time import time
from uuid import uuid4
from textwrap import dedent
from urllib.parse import urlparse
from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # Using set to hold the list of nodes
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)
    
    # Determine if the given blockchain is valid
    # this methond loops through each block and verifies
    # using both hash and proof
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n===========")

            # Check if the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            # Check if the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            
            last_block = block
            current_index += 1
        return True

    # This is our Consensus Algorithm which resolves conflicts
    # by replacing our chain with the longest one in the network.
    # Returns True if our chain was replaced, False if not
    # This method loops through all our neighour nodes to find a 
    # longer and valid chain
    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        # We are now looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from the all the nodes
        # in our network

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Lets check if the length is longer and chain is valid

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
                
        # Replace our chain with the longer and valid chain we discovered

        if new_chain:
            self.chain = new_chain
            return True
        
        return False



    # Function to add new node to the list of nodes
    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # Function to create new Block and adds it to the chain
    def new_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        self.current_transactions = []
        self.chain.append(block)
        return block
    
    # Function to add a new transaction to the list of transactoins
    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount':amount
        })
        return self.last_block['index'] + 1

    # Hashes a block
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # Returns the last block in the chain
    @property
    def last_block(self):
        return self.chain[-1]
    
    # Implement proof of work
    def proof_of_work(self, last_proof):
        # PoW algorithm here is:
        # - Find a number 'p' that when hashed with previous block's proof, 
        #   a hash is produced with 4 leading 0s

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof
    @staticmethod
    def valid_proof(last_proof, proof):
        # validates if hash (last_proof,proof) contains 4 leading zeroes?
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# I will use Flask framework to map endpoints to python functions; 
# hence allowing us to talk to our blockchain over the web using HHTP requests
# I will create four methods:
# /transactions : to tell total number of transactions
# /transactions/new: to create new transaction to the block
# /mine: to tell our service to mine a new block
# /chain: to return full blockchain

# Instantiate our Node
app = Flask(__name__)

    # Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-','')

    # Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/', methods=['GET'])
def start():
    return "Lets Start!"

@app.route('/mine', methods=['GET'])
def mine():
    # Calculate the proof of work
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Reward the miner by granting us 1 coin
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender = "0",
        recipient=node_identifier,
        amount = 1
    )
    # Create the new block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'New Block Added!',
        'index': block['index'],
        'transaction': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200

@app.route('/transactions', methods=['GET'])
def total_transactions():
        return "We have got so many transactions"
    
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    # Check that the required fields are in the request
    required = ['sender', 'recipient', 'amount']
    if not all (k in values for k in required):
        return "Missing values", 
    
    # Create a new Transaction
    index = blockchain.new_transaction(
        values['sender'],
        values['recipient'],
        values['amount']
    )

    response = {'message': f'Transaction will be added to the block {index}'}
    return jsonify(response), 200



@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)
    
    response = {
        'message' : 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consenses():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Our blockchain has been replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our blockchain is authoritive',
            'chain': blockchain.chain
        }
    return jsonify(response), 200



@app.route('/chain', methods=['GET'])
def full_chain():
        response = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain)
        }
        return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p',
     '--port', 
     default=5000, 
     type=int, 
     help='port to listen on')
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port)






    

        
