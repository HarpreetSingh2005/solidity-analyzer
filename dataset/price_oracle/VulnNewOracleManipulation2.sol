// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Using address(this).balance as an oracle for lending.
contract VulnNewOracleManipulation2 {
    function getMaxBorrow(uint256 collateral) public view returns (uint256) {
        uint256 vaultBalance = address(this).balance; // Easily flash-loanable
        return (collateral * vaultBalance) / 1000;
    }
}