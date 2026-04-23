// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract GhostCollateral {
    mapping(address => uint256) public collateral;
    function depositCollateral() external payable {
        collateral[msg.sender] += msg.value;
    }
    function borrow(uint256 amount) external {
        require(collateral[msg.sender] >= amount, "Insufficient collateral");
        payable(msg.sender).transfer(amount);
    }
}