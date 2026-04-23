// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnOracleManipulationLending {
    mapping(address => uint256) public collateral;
    mapping(address => uint256) public borrowed;

    // Vulnerability: Borrows based on manipulated spot balance of the contract
    function borrow(uint256 amount) external {
        uint256 spotPrice = address(this).balance; // Easily manipulated by forced ETH transfer
        uint256 maxBorrow = collateral[msg.sender] * spotPrice / 1e18;
        
        require(borrowed[msg.sender] + amount <= maxBorrow, "Exceeds max borrow");
        borrowed[msg.sender] += amount;
    }
}