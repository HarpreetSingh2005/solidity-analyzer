// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnVaultInflation {
    uint256 public totalShares;
    mapping(address => uint256) public shares;

    // Vulnerability: Empty vault inflation attack (donation attack)
    function deposit() external payable {
        uint256 sharesToMint;
        if (totalShares == 0) {
            sharesToMint = msg.value;
        } else {
            // Attacker can manipulate address(this).balance by direct transfer before deposit
            sharesToMint = (msg.value * totalShares) / (address(this).balance - msg.value);
        }
        shares[msg.sender] += sharesToMint;
        totalShares += sharesToMint;
    }
}