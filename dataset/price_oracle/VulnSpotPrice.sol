// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IUniswapV2Pair {
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast);
}

contract VulnSpotPrice {
    IUniswapV2Pair public pair;

    // Vulnerability: Relies on easily manipulable spot price from reserves
    function getPrice() public view returns (uint256) {
        (uint112 reserve0, uint112 reserve1, ) = pair.getReserves();
        return uint256(reserve1) * 1e18 / uint256(reserve0);
    }
}