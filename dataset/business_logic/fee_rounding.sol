// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract FeeRounding {
    uint256 public constant FEE_BPS = 30; // 0.3%
    function swap(uint256 amount) external pure returns (uint256 net, uint256 fee) {
        fee = (amount * FEE_BPS) / 10000; // BUG: rounds to 0 for small amounts
        net = amount - fee;
    }
}