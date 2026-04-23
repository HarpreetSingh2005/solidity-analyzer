// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IUniswapV3Pool {
    function observe(uint32[] calldata secondsAgos) external view returns (int56[] memory tickCumulatives, uint160[] memory secondsPerLiquidityCumulativeX128s);
}

contract VulnShortTWAP {
    IUniswapV3Pool public pool;

    // Vulnerability: TWAP window is extremely short (1 second), effectively a spot price
    function getShortTWAP() public view returns (int24 tick) {
        uint32[] memory secondsAgos = new uint32[](2);
        secondsAgos[0] = 1; // 1 second ago
        secondsAgos[1] = 0; // now

        (int56[] memory tickCumulatives, ) = pool.observe(secondsAgos);
        tick = int24((tickCumulatives[1] - tickCumulatives[0]) / 1);
    }
}