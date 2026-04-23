// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeLending {
    mapping(address => uint256) public collateral;
    mapping(address => uint256) public borrowed;

    function depositCollateral() external payable {
        collateral[msg.sender] += msg.value;
    }

    function borrow(uint256 amount) external {
        require(collateral[msg.sender] >= amount * 2, "Insufficient collateral");
        borrowed[msg.sender] += amount;
        payable(msg.sender).transfer(amount);
    }
}