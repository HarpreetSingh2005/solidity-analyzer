// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract DecimalMismatch {
    function getPrice() public pure returns (uint256) {
        return 100000000; // BUG: 8 decimals treated as 18
    }
}