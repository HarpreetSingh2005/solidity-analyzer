// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract CrossFuncReentrancy {
    mapping(address => uint256) public deposited;
    function withdraw(uint256 amount) external {
        (bool ok,) = msg.sender.call{value: amount}("");
        deposited[msg.sender] -= amount;
    }
}