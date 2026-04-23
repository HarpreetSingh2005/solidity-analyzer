// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IUniswapV2Pair { function getReserves() external view returns (uint112, uint112, uint32); }
// Vulnerability: Manipulable spot price oracle.
contract VulnNewOracleSpot1 {
    IUniswapV2Pair public pair;
    function getPrice() public view returns (uint256) {
        (uint112 reserve0, uint112 reserve1, ) = pair.getReserves();
        return uint256(reserve1) * 1e18 / uint256(reserve0); // Flash loan can skew this
    }
}