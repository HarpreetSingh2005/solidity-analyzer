// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Vulnerable to Flash Loan manipulation. Shares rely on manipulatable spot balance.
contract TestVulnFlashLoan {
    uint256 public totalShares;
    
    // Vulnerable: Shares minted based on manipulatable address(this).balance
    function deposit() external payable {
        uint256 shares;
        if (totalShares == 0) {
            shares = msg.value;
        } else {
            // Attacker can flash loan ETH to themselves and force-send it to inflate address(this).balance
            shares = (msg.value * totalShares) / (address(this).balance - msg.value);
        }
        totalShares += shares;
    }
}