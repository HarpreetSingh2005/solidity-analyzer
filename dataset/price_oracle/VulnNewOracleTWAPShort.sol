// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IUniswapV3Pool { function observe(uint32[] calldata) external view returns (int56[] memory, uint160[] memory); }
// Vulnerability: TWAP window is 1 second, making it functionally equivalent to a manipulatable spot price.
contract VulnNewOracleTWAPShort {
    IUniswapV3Pool public pool;
    function getPrice() public view returns (int24 tick) {
        uint32[] memory agos = new uint32[](2);
        agos[0] = 1; agos[1] = 0;
        (int56[] memory ticks, ) = pool.observe(agos);
        tick = int24((ticks[1] - ticks[0]) / 1);
    }
}