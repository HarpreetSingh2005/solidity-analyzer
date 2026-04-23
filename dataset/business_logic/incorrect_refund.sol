// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract IncorrectRefund {
    mapping(address => uint256) public contributions;
    function refund() external {
        uint256 amount = contributions[msg.sender];
        contributions[msg.sender] = 0;
        payable(msg.sender).transfer(amount); // BUG: double refund possible if called twice
    }
}