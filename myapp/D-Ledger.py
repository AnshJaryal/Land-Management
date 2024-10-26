import json
import time
import hashlib
import mysql.connector
from web3 import Web3

# Ethereum se connect kr
infura_url = 'https://mainnet.infura.io/v3/251315b2f23f4439b86206e0bfd79df3'  # replace with your Infura project ID
web3 = Web3(Web3.HTTPProvider(infura_url))

if web3.is_connected():  # connection check kr
    print("Successfully connected to Ethereum")
else:
    print("Failed to connect to Ethereum")


# MySQL database connection
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="bdj393825@!",  # Replace with your MySQL password
            database="blockchain_ledger"  # Ensure this database is created
        )
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


# Store block hash in MySQL database
def store_block_hash_in_db(block_hash, block_number):
    connection = connect_db()
    if connection:
        cursor = connection.cursor()

        # Check if block with given block_number already exists
        cursor.execute("SELECT * FROM blocks WHERE block_number = %s", (block_number,))
        existing_block = cursor.fetchone()

        # If block doesn't exist, insert it
        if not existing_block:
            cursor.execute("""
                INSERT INTO blocks (block_number, block_hash)
                VALUES (%s, %s)
            """, (block_number, block_hash))
            connection.commit()
            print(f"Block {block_number} hash saved to MySQL")
        else:
            print(f"Block {block_number} already exists in the database")

        cursor.close()
        connection.close()



# Fetch all block hashes from MySQL
def fetch_block_hashes():
    connection = connect_db()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM blocks")
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result


class Block:
    def __init__(self, previous_hash, data, timestamp=None):
        self.timestamp = timestamp or time.time()
        self.data = data  # Land details (address, size, dimensions, owner)
        self.previous_hash = previous_hash  # Link to the previous block's hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_content = json.dumps(self.data, sort_keys=True) + str(self.previous_hash) + str(self.timestamp)
        return hashlib.sha256(block_content.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        genesis_data = {
            "land_address": "Genesis Block",  # Starting block data
            "land_size": "0",
            "land_dimensions": "0x0",
            "owner": "None"
        }
        genesis_block = Block("0", genesis_data)
        self.chain = [genesis_block]
        store_block_hash_in_db(genesis_block.hash, 0)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        previous_hash = self.get_latest_block().hash  # Get hash of the previous block
        new_block = Block(previous_hash, data)
        self.chain.append(new_block)
        store_block_hash_in_db(new_block.hash, len(self.chain) - 1)  # Save to MySQL

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Check if current block's hash is valid
            if current_block.hash != current_block.calculate_hash():
                return False

            # Check if previous block's hash matches
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def print_chain(self):
        for block in self.chain:
            print(f"Block Hash: {block.hash}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Data: {block.data}")
            print(f"Timestamp: {block.timestamp}\n")

    def recalculate_chain(self):
        """Recalculates the hash for the entire chain after ownership change"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            current_block.previous_hash = self.chain[i - 1].hash  # Re-link to new previous hash
            current_block.hash = current_block.calculate_hash()  # Recalculate the hash


# Create blockchain
land_chain = Blockchain()

# Register 5 homes in Rajouri Garden with anonymous owners (landlord1, landlord2, etc.)
land_data_1 = {
    "land_address": "123 Rajouri Garden",
    "land_size": "500 sqm",
    "land_dimensions": "25x20",
    "owner": "landlord1"
}
land_chain.add_block(land_data_1)

land_data_2 = {
    "land_address": "124 Rajouri Garden",
    "land_size": "550 sqm",
    "land_dimensions": "27x20",
    "owner": "landlord2"
}
land_chain.add_block(land_data_2)

land_data_3 = {
    "land_address": "125 Rajouri Garden",
    "land_size": "450 sqm",
    "land_dimensions": "22x20",
    "owner": "landlord3"
}
land_chain.add_block(land_data_3)

land_data_4 = {
    "land_address": "126 Rajouri Garden",
    "land_size": "600 sqm",
    "land_dimensions": "30x20",
    "owner": "landlord4"
}
land_chain.add_block(land_data_4)

land_data_5 = {
    "land_address": "127 Rajouri Garden",
    "land_size": "700 sqm",
    "land_dimensions": "35x20",
    "owner": "landlord5"
}
land_chain.add_block(land_data_5)

# Print the chain
land_chain.print_chain()

# Now simulate a change in ownership of Block 1
print("---- Ownership Change in Block 1 ----")
land_chain.chain[1].data['owner'] = "new_owner1"

# Recalculate the entire chain
land_chain.recalculate_chain()

# Print the new chain after recalculating
land_chain.print_chain()

# Fetch block hashes from the database (for validation if needed)
block_hashes_from_db = fetch_block_hashes()
print("Stored Block Hashes in MySQL:")
print(block_hashes_from_db)

# Check if the blockchain is still valid after the change
if land_chain.is_chain_valid():
    print("Blockchain is valid and secure.")
else:
    print("Blockchain is invalid.")
