// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeBridge {
    mapping(address => uint256) public locked;

    function lock(uint256 amount) external payable {
        locked[msg.sender] += amount;
    }

    function unlock(uint256 amount) external {
        require(locked[msg.sender] >= amount);
        locked[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);
    }
}