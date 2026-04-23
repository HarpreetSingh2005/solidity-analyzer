// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract BridgeOrdering {
    function bridgeIn(address recipient, uint256 amount, bytes32 proof) external {
        // BUG: mint before proof verification
        // mint(recipient, amount);
        require(proof != bytes32(0), "Invalid proof");
    }
}