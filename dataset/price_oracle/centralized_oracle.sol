// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Fully Centralized Oracle (Single Point of Failure)
 * CATEGORY: Price Oracle — Centralization / No Fallback
 *
 * A single admin wallet controls all price feeds with no time-lock,
 * no multi-sig, no on-chain fallback, and no deviation check between
 * updates. This is the #1 exploit vector in DeFi: compromised deployer
 * key → instant drain of all funds via price manipulation + borrowing.
 */
contract CentralizedOracle {
    address public owner;
    mapping(address => uint256) public prices;      // token → USD price (18 dec)
    mapping(address => uint256) public lastUpdated;

    event PriceUpdated(address indexed token, uint256 price);

    constructor() {
        owner = msg.sender;
    }

    // BUG: single EOA controls all prices, no time-lock, no deviation check
    function setPrice(address token, uint256 price) external {
        require(msg.sender == owner, "Not owner");
        // BUG: no check that price changed by <= X% from previous
        // BUG: no minimum delay between updates
        // BUG: no multi-sig or governance
        prices[token]      = price;
        lastUpdated[token] = block.timestamp;
        emit PriceUpdated(token, price);
    }

    function getPrice(address token) external view returns (uint256) {
        require(prices[token] > 0, "Price not set");
        // BUG: no staleness check — price could be weeks old
        return prices[token];
    }

    // BUG: owner can transfer oracle control to any address with no delay
    function transferOwnership(address newOwner) external {
        require(msg.sender == owner);
        owner = newOwner;
    }
}
