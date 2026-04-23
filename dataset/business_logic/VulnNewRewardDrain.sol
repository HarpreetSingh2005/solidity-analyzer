// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Rewards can be claimed multiple times because the state is not updated before transfer.
contract VulnNewRewardDrain {
    mapping(address => uint256) public rewards;
    function claimReward() external {
        uint256 amount = rewards[msg.sender];
        require(amount > 0, "No reward");
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Failed");
        rewards[msg.sender] = 0; // State updated after interaction
    }
}