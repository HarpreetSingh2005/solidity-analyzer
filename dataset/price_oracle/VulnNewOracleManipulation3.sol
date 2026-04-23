// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Yield calculation depends on easily flash-loanable external balance.
contract VulnNewOracleManipulation3 {
    function getYieldRate() public view returns (uint256) {
        // Reads balance of some token in some external protocol
        return 100; // placeholder for manipulatable external state
    }
}