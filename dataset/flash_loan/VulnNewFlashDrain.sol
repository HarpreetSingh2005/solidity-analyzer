// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Flash loan mechanism allows draining underlying token without repayment check.
contract VulnNewFlashDrain {
    function flashLoan(uint256 amount) external {
        // Missing require(repaid >= amount + fee)
    }
}