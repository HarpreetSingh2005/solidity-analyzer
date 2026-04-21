// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: AMM Liquidity Drain via Flash Loan + Sandwich
 * CATEGORY: Flash Loan — Liquidity Pool Drain
 *
 * The AMM uses a constant-product invariant (x*y=k) but does not collect
 * a swap fee. An attacker can use a flash loan to:
 * 1. Drain all of token0 by repeated swaps (k maintained, but all token0 extracted)
 * 2. The last swap at extreme imbalance extracts near-zero token1 per token0
 * 3. Restore token1 to repay flash loan
 * Without fees, there is no economic disincentive — the pool is drained.
 */
contract LiquidityDrain {
    uint256 public reserve0;
    uint256 public reserve1;
    mapping(address => uint256) public lpBalance;
    uint256 public totalLp;

    // BUG: no swap fee — AMM is economically drainable
    function swap0For1(uint256 amount0In) external returns (uint256 amount1Out) {
        require(amount0In > 0, "Zero input");
        // constant product: (r0 + in) * (r1 - out) = r0 * r1
        amount1Out = (reserve1 * amount0In) / (reserve0 + amount0In);
        require(amount1Out > 0, "Zero output");
        reserve0 += amount0In;
        reserve1 -= amount1Out;
        // BUG: no fee → attacker can drain token1 for free via incremental swaps
    }

    function addLiquidity(uint256 amount0, uint256 amount1) external payable {
        reserve0 += amount0;
        reserve1 += amount1;
        uint256 lp = totalLp == 0 ? 1000 : (amount0 * totalLp) / reserve0;
        lpBalance[msg.sender] += lp;
        totalLp               += lp;
    }

    function removeLiquidity(uint256 lp) external {
        require(lpBalance[msg.sender] >= lp, "Insufficient LP");
        uint256 amt0 = (lp * reserve0) / totalLp;
        uint256 amt1 = (lp * reserve1) / totalLp;
        lpBalance[msg.sender] -= lp;
        totalLp               -= lp;
        reserve0              -= amt0;
        reserve1              -= amt1;
        payable(msg.sender).transfer(amt0 + amt1);
    }

    receive() external payable {}
}
