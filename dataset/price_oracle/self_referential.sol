// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Self-Referential Price Oracle
 * CATEGORY: Price Oracle — Circular / Manipulatable Reserve Ratio
 *
 * The protocol uses its own internal ETH:Token reserve ratio as the price
 * oracle. This is the same pool that users trade against. Anyone who can
 * perform a large trade (or flash loan) can set an arbitrary price, then
 * use that price to borrow inflated amounts from the lending module.
 */
contract SelfReferentialOracle {
    uint256 public ethReserve;
    uint256 public tokenReserve;
    mapping(address => uint256) public tokenBalance;
    mapping(address => uint256) public ethDeposited;

    // BUG: price is THIS contract's own reserve ratio — directly manipulatable
    function getTokenPrice() public view returns (uint256) {
        require(tokenReserve > 0, "No liquidity");
        return (ethReserve * 1e18) / tokenReserve;  // ETH per token
    }

    function addLiquidity(uint256 tokenAmount) external payable {
        ethReserve   += msg.value;
        tokenReserve += tokenAmount;
        tokenBalance[msg.sender] += tokenAmount;
    }

    // Swap ETH for tokens — also shifts the price!
    function swapEthForTokens(uint256 minTokens) external payable {
        uint256 tokens = (msg.value * tokenReserve) / ethReserve;
        require(tokens >= minTokens, "Slippage");
        ethReserve   += msg.value;
        tokenReserve -= tokens;
        tokenBalance[msg.sender] += tokens;
    }

    // BUG: borrow limit derived from the manipulatable self-referential price
    function borrowAgainstToken(uint256 tokenAmount) external {
        uint256 collateralValue = (tokenAmount * getTokenPrice()) / 1e18;
        uint256 borrowable      = (collateralValue * 75) / 100;
        tokenBalance[msg.sender] -= tokenAmount;
        payable(msg.sender).transfer(borrowable);
    }

    receive() external payable { ethReserve += msg.value; }
}
