// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe bridge contract utilizing ecrecover correctly to prevent replay attacks.
contract SafeBridge {
    address public validator;
    mapping(bytes32 => bool) public processedNonces;

    event TokensUnlocked(address indexed to, uint256 amount);

    constructor(address _validator) {
        validator = _validator;
    }

    function unlockTokens(address to, uint256 amount, bytes32 nonce, bytes memory signature) external {
        require(!processedNonces[nonce], "Nonce already processed");
        
        bytes32 messageHash = keccak256(abi.encodePacked(to, amount, nonce));
        bytes32 ethSignedMessageHash = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", messageHash));
        
        require(recoverSigner(ethSignedMessageHash, signature) == validator, "Invalid signature");

        processedNonces[nonce] = true;
        
        emit TokensUnlocked(to, amount);
    }

    function recoverSigner(bytes32 _ethSignedMessageHash, bytes memory _signature) internal pure returns (address) {
        require(_signature.length == 65, "Invalid signature length");
        bytes32 r;
        bytes32 s;
        uint8 v;
        assembly {
            r := mload(add(_signature, 32))
            s := mload(add(_signature, 64))
            v := byte(0, mload(add(_signature, 96)))
        }
        return ecrecover(_ethSignedMessageHash, v, r, s);
    }
}