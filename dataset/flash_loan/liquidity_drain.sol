// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract LiquidityDrain {
    uint256 public reserve0;
    uint256 public reserve1;
    function swap(uint256 amount) external {
        reserve0 += amount;
        reserve1 -= amount; // BUG: no fee, drainable
    }
}