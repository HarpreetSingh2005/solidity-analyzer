// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
interface IUniswapV2Pair { function getReserves() external view returns (uint112, uint112, uint32); }
contract SpotPriceOracle {
    IUniswapV2Pair public pair;
    constructor(address _pair) { pair = IUniswapV2Pair(_pair); }
    function getPrice() public view returns (uint256) {
        (uint112 r0, uint112 r1,) = pair.getReserves();
        return (uint256(r1) * 1e18) / uint256(r0); // BUG: manipulatable spot price
    }
}