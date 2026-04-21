// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Protocol Fee Bypass via Circular Flash Loan
 * CATEGORY: Flash Loan — Economic Invariant Violation
 *
 * The protocol charges a 1% fee on withdrawals. An attacker can:
 * 1. Flash borrow enough to cover their withdrawal
 * 2. Deposit the flash-loaned funds (earns shares at current price)
 * 3. Withdraw original position (fee waived because they "just deposited")
 * 4. Repay flash loan with the withdrawn funds
 * Result: original withdrawal is fee-free.
 *
 * The fee waiver condition (deposited in same block) creates the bypass.
 */
contract FeeBypassFlashloan {
    mapping(address => uint256) public shares;
    mapping(address => uint256) public lastDepositBlock;
    uint256 public totalShares;
    uint256 public totalAssets;
    uint256 public constant FEE_BPS = 100; // 1% withdrawal fee

    function deposit() external payable {
        uint256 newShares = totalShares == 0
            ? msg.value
            : (msg.value * totalShares) / totalAssets;
        shares[msg.sender]         += newShares;
        totalShares                += newShares;
        totalAssets                += msg.value;
        lastDepositBlock[msg.sender] = block.number; // BUG: enables fee bypass in same block
    }

    function withdraw(uint256 shareAmount) external {
        require(shares[msg.sender] >= shareAmount, "Insufficient");
        uint256 ethAmount = (shareAmount * totalAssets) / totalShares;
        shares[msg.sender] -= shareAmount;
        totalShares        -= shareAmount;
        totalAssets        -= ethAmount;

        // BUG: fee waived if deposited in this block — easily abused with flash loans
        uint256 fee = (lastDepositBlock[msg.sender] == block.number)
            ? 0
            : (ethAmount * FEE_BPS) / 10_000;
        payable(msg.sender).transfer(ethAmount - fee);
    }

    receive() external payable {}
}
