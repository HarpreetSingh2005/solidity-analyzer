// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeReward {
    mapping(address => uint256) public rewards;

    function claimReward() external {
        uint256 amount = rewards[msg.sender];
        rewards[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }
}