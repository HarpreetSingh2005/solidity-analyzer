// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe Airdrop contract using Merkle tree proof verification.
contract SafeAirdrop {
    bytes32 public merkleRoot;
    mapping(address => bool) public hasClaimed;

    constructor(bytes32 _merkleRoot) {
        merkleRoot = _merkleRoot;
    }

    function claim(uint256 amount, bytes32[] calldata merkleProof) external {
        require(!hasClaimed[msg.sender], "Already claimed");
        
        bytes32 node = keccak256(abi.encodePacked(msg.sender, amount));
        require(verifyProof(merkleProof, merkleRoot, node), "Invalid proof");

        hasClaimed[msg.sender] = true;
        // Token transfer logic here
    }

    function verifyProof(bytes32[] memory proof, bytes32 root, bytes32 leaf) internal pure returns (bool) {
        bytes32 computedHash = leaf;

        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 proofElement = proof[i];

            if (computedHash <= proofElement) {
                computedHash = keccak256(abi.encodePacked(computedHash, proofElement));
            } else {
                computedHash = keccak256(abi.encodePacked(proofElement, computedHash));
            }
        }

        return computedHash == root;
    }
}