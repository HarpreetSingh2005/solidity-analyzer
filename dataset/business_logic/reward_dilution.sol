// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract RewardDilution {
    mapping(address => uint256) public rewards;
    uint256 public totalStaked;
    function stake(uint256 amount) external {
        totalStaked += amount;
        // BUG: new staker dilutes existing rewards without proper checkpoint
    }
}