// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnSigReplay {
    mapping(address => uint256) public balances;
    
    // Vulnerability: Replay attack possible due to missing nonce or specific ID
    function transferWithSignature(address to, uint256 amount, bytes memory signature) external {
        bytes32 messageHash = keccak256(abi.encodePacked(to, amount));
        bytes32 ethSignedMessageHash = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", messageHash));
        
        address signer = recoverSigner(ethSignedMessageHash, signature);
        require(balances[signer] >= amount, "Insufficient balance");
        
        balances[signer] -= amount;
        balances[to] += amount;
    }

    function recoverSigner(bytes32 hash, bytes memory signature) internal pure returns (address) {
        bytes32 r; bytes32 s; uint8 v;
        if (signature.length != 65) return address(0);
        assembly {
            r := mload(add(signature, 32))
            s := mload(add(signature, 64))
            v := byte(0, mload(add(signature, 96)))
        }
        return ecrecover(hash, v, r, s);
    }
}