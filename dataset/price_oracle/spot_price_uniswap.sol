// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Uniswap V2 Spot Price as Oracle
 * CATEGORY: Price Oracle — Single-Block Manipulation
 *
 * Reads getReserves() directly from the Uniswap V2 pair to compute price.
 * Within a single transaction, an attacker can use a flash loan to move
 * the reserves drastically (dump one token), call this contract to borrow
 * against the manipulated price, then restore reserves — all in one tx.
 */
interface IUniswapV2Pair {
    function getReserves() external view returns (uint112 r0, uint112 r1, uint32 ts);
}

contract SpotPriceOracle {
    IUniswapV2Pair public immutable pair;
    address        public immutable lendingPool;

    constructor(address _pair, address _pool) {
        pair        = IUniswapV2Pair(_pair);
        lendingPool = _pool;
    }

    // BUG: spot price — manipulatable within a single transaction
    function getPrice() public view returns (uint256) {
        (uint112 r0, uint112 r1,) = pair.getReserves();
        require(r0 > 0 && r1 > 0, "Empty reserves");
        // price of token0 in terms of token1 (scaled 1e18)
        return (uint256(r1) * 1e18) / uint256(r0);
    }

    function getCollateralValue(uint256 tokenAmount) external view returns (uint256) {
        // BUG: price is from manipulatable spot — used to determine borrow limit
        return (tokenAmount * getPrice()) / 1e18;
    }
}
