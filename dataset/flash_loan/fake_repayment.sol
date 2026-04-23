// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract FakeRepayment {
    function flashLoan(uint256 amount) external {
        // BUG: fake repayment via internal deposit
    }
}