// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeVesting {
    mapping(address => uint256) public vestedAmount;
    uint256 public startTime;

    constructor() {
        startTime = block.timestamp;
    }

    function vest(uint256 amount) public {
        vestedAmount[msg.sender] = amount;
    }

    function claim() public {
        require(block.timestamp >= startTime + 30 days, "Vesting not over");
        uint256 amount = vestedAmount[msg.sender];
        vestedAmount[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }
}