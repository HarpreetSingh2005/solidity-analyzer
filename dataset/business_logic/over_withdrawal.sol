// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract OverWithdrawal {
    mapping(address => uint256) public balance;
    function withdraw(uint256 amount) external {
        require(balance[msg.sender] >= amount);
        balance[msg.sender] -= amount;
        payable(msg.sender).transfer(amount * 2); // BUG: over-withdrawal
    }
}