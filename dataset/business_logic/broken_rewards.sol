// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract BrokenRewards {
    mapping(address => uint256) public staked;
    uint256 public totalStaked;
    uint256 public totalRewards;
    function deposit(uint256 amount) external { staked[msg.sender] += amount; totalStaked += amount; }
    function addRewards(uint256 amount) external { totalRewards += amount; }
    function claim() external {
        uint256 pending = (totalRewards * staked[msg.sender]) / totalStaked; // BUG: integer division rounding loss
        payable(msg.sender).transfer(pending);
    }
}