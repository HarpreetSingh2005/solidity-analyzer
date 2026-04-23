// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Staking rewards distributed based on spot balance, drained by flash loan.
contract VulnNewFlashReward {
    function claim() external payable {
        // Can flash loan, deposit, and immediately claim massive rewards
        uint256 reward = (msg.value * 10) / 100;
        payable(msg.sender).transfer(reward);
    }
}