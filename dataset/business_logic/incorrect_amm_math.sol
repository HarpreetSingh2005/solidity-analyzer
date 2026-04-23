// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract IncorrectAMM {
    uint256 public reserve0;
    uint256 public reserve1;
    function swap(uint256 amount0In) external {
        uint256 amount1Out = (reserve1 * amount0In) / (reserve0 + amount0In);
        reserve0 += amount0In;
        reserve1 -= amount1Out;
    }
}