// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashStakingReward {
    mapping(address => uint256) public stakes;

    // Vulnerability: Reward is instantly calculated based on current spot balance
    function stakeAndClaim() external payable {
        stakes[msg.sender] += msg.value;
        
        // Spot reward calculation allows flash loan to drain rewards
        uint256 reward = address(this).balance / 100;
        payable(msg.sender).transfer(reward);
    }
}