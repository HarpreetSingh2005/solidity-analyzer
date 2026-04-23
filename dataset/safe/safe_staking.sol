// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeStaking {
    mapping(address => uint256) public staked;
    uint256 public totalStaked;

    function stake() external payable {
        staked[msg.sender] += msg.value;
        totalStaked += msg.value;
    }

    function unstake(uint256 amount) external {
        require(staked[msg.sender] >= amount, "Insufficient stake");
        staked[msg.sender] -= amount;
        totalStaked -= amount;
        payable(msg.sender).transfer(amount);
    }
}