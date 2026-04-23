// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IUniswapV2Pair {
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast);
}

contract VulnFlashOracle {
    IUniswapV2Pair public pair;

    // Vulnerability: Flash loan can heavily skew reserves to return a manipulated price
    function getPrice() external view returns (uint256) {
        (uint112 reserve0, uint112 reserve1, ) = pair.getReserves();
        return uint256(reserve0) / uint256(reserve1);
    }
}