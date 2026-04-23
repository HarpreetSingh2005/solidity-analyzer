// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeDEX {
    uint256 public reserve0;
    uint256 public reserve1;

    function addLiquidity(uint256 amount0, uint256 amount1) external {
        reserve0 += amount0;
        reserve1 += amount1;
    }

    function swap(uint256 amount0In) external {
        uint256 amount1Out = (reserve1 * amount0In) / (reserve0 + amount0In);
        reserve0 += amount0In;
        reserve1 -= amount1Out;
        payable(msg.sender).transfer(amount1Out);
    }
}