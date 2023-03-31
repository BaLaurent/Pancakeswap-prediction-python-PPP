# Pancakeswap-prediction-python-PPP

This Python script is a betting bot for the BSC Prediction Market. It interacts with the Prediction Market smart contract and places bets on BULL or BEAR based on the current price fetched from an oracle. It also claims winnings, and sends bet notifications to a Discord channel using webhooks.

## Dependencies

- web3
- discord_webhook

## Setup

1. Install the required Python packages:
```
pip install web3 discord-webhook
```

2. Create a `config.json` file in the same directory as the script with the following structure:

```json
{
    "privateKey": "YOUR_PRIVATE_KEY",
    "publicKey": "YOUR_PUBLIC_KEY",
    "betAmt": 0.1,
    "gweiGas": 5,
    "webHookUrl": "YOUR_DISCORD_WEBHOOK_URL"
}
```

- Replace YOUR_PRIVATE_KEY with your wallet's private key.
- Replace YOUR_PUBLIC_KEY with your wallet's public key.
- Replace YOUR_DISCORD_WEBHOOK_URL with your Discord webhook URL.

## Usage

To use the bot, instantiate the `pcsInteraction` class and call the desired methods. Here's a brief overview of the available methods:

- `betBull()`: Places a bet on BULL for the current epoch.
- `betBear()`: Places a bet on BEAR for the current epoch.
- `getBalance()`: Returns the current balance of the wallet in BNB.
- `getOraclePrice()`: Fetches the current oracle price.
- `currentEpoch()`: Returns the current epoch.
- `userLastRounds(length=1)`: Returns the user's betting history for the specified number of rounds.
- `isClaimable(roundId)`: Checks if the winnings from the specified round are claimable.
- `claim()`: Claims the winnings from the last round if available.
- `getTimeLeft()`: Returns the time left in seconds for the current epoch.

### Example

```python
from pcs_interaction import pcsInteraction

# Instantiate the class
bot = pcsInteraction()

# Bet BULL
bot.betBull()

# Bet BEAR
bot.betBear()

# Claim winnings
bot.claim()

```
