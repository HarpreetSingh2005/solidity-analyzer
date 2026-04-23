// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IERC20 { function transferFrom(address, address, uint256) external returns (bool); }
// Vulnerability: Unchecked ERC20 transferFrom return value.
contract VulnNewUncheckedTransfer {
    function deposit(IERC20 token, uint256 amount) external {
        // Doesn't check if transferFrom returns true or false
        token.transferFrom(msg.sender, address(this), amount);
    }
}