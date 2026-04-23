// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: LP token pricing manipulated via read-only reentrancy during removeLiquidity.
contract VulnNewOracleManipulation4 {
    function getLPPrice() public pure returns (uint256) {
        // Vulnerable to read-only reentrancy if target pool state is not updated before external call
        return 1e18;
    }
}