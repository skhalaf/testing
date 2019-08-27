const steem = require("steem");
const fetch = require("node-fetch");
const md5 = require("md5");
const KEYS = require("./keys.json");
const cardData = require("./cardData.json");
function possibleCards(splinter, battle = {}) {
  return cardData.filter(card => {
    if (card.type !== "Monster") return;
    if ((card.color !== splinter) && (card.color !== "Gray")) return;
    if (battle.ruleset === "Lost Legendaries" && card.rarity === 4) return;
    if (battle.ruleset === "Rise of the Commons" && card.rarity > 2) return;
    if (battle.ruleset === "Taking Sides" && card.color === "Gray") return;
    //these should actually take in to account the level of the card. creeping ooze becomes a melee monster @ level 4, but this never allows it
    if (battle.ruleset === "Up Close & Personal" && card.stats.attack[0] === 0) return;
    if (battle.ruleset === "Broken Arrows" && card.stats.ranged[card.stats.ranged.length - 1] > 0) return;
    if (battle.ruleset === "Little League" && (card.stats.mana[0] > 4)) return;
    return true;
  });
};
function cardBcx(xp, rarity, edition, gold) {
        if (edition === 3) edition = 1; //reward cards are same as beta
        var cards = 0;
        if (edition == 0 && gold == 0 && rarity == 4)
            cards = (xp / 1000) +1
        if (edition == 0 && gold == 0 && rarity == 3)
            cards = (xp / 250) +1
        if (edition == 0 && gold == 0 && rarity == 2)
            cards = (xp / 100) +1
        if (edition == 0 && gold == 0 && rarity == 1)
            cards = (xp / 20) +1
        if (edition == 0 && gold == 1 && rarity == 4)
            cards = xp / 2500
        if (edition == 0 && gold == 1 && rarity == 3)
            cards = xp / 1000
        if (edition == 0 && gold == 1 && rarity == 2)
            cards = xp / 500
        if (edition == 0 && gold == 1 && rarity == 1)
            cards = xp / 250

        // Beta Edition Cards per XP
        if (edition == 1 && gold == 0 && rarity == 4)
            cards = (xp / 750) +1
        if (edition == 1 && gold == 0 && rarity == 3)
            cards = (xp / 175) +1
        if (edition == 1 && gold == 0 && rarity == 2)
            cards = (xp / 75) +1
        if (edition == 1 && gold == 0 && rarity == 1)
            cards = (xp / 15) +1
        if (edition == 1 && gold == 1 && rarity == 4)
            cards = xp / 2000
        if (edition == 1 && gold == 1 && rarity == 3)
            cards = xp / 800
        if (edition == 1 && gold == 1 && rarity == 2)
            cards = xp / 400
        if (edition == 1 && gold == 1 && rarity == 1)
            cards = xp / 200
        // Promo Edition Cards per XP
        if (edition == 2 && gold == 0 && rarity == 4)
            cards = (xp / 1000) +1
        if (edition == 2 && gold == 0 && rarity == 3)
            cards = (xp / 250) +1
        if (edition == 2 && gold == 0 && rarity == 2)
            cards = (xp / 100) +1
        if (edition == 2 && gold == 0 && rarity == 1)
            cards = (xp / 20) +1
        if (edition == 2 && gold == 1 && rarity == 4)
            cards = xp / 2500
        if (edition == 2 && gold == 1 && rarity == 3)
            cards = xp / 1000
        if (edition == 2 && gold == 1 && rarity == 2)
            cards = xp / 500
        if (edition == 2 && gold == 1 && rarity == 1)
            cards = xp / 250
        if (cards === 0) throw new Error("Unable to find card BCX");
        return cards
      }


class Battle {
  constructor(callback, appName = "smitopbot-public/1.0.0", matchType = "Ranked") {
    this.callback = callback;
    this.status = {};
    this.submittedTeam = false;
    //broadcast sm_find_match
    steem.broadcast.customJson(KEYS.posting, [], [KEYS.username], "sm_find_match", JSON.stringify({
      match_type: matchType,
      app: appName
    }), (err, result) => {
      if (err) throw err;
      console.log("Broadcasted sm_find_match");
      this.findMatchId = result.id;
    });
    //start /battle/status check loop
    this._checkInterval = setInterval(() => {
      this._checkBattleStatus();
    }, 2500);
    //
  }
  end() {
    this.ended = true;
    clearInterval(this._checkInterval);
    delete this;
  }
  setTeam(team) {
    this.team = team;
  }
  broadcastTeam(summoner, monsters, skipReveal = false) {
    const secret = Battle.generatePassword();
    const teamHash = md5(summoner + "," + monsters.join() + "," + secret)
    const team = {summoner, monsters, secret};

    this.submittedTeam = true;
    var data = {
      trx_id: this.findMatchId,
      team_hash: teamHash,
      app: this.appName
    };
    if (skipReveal) {
      data.summoner = summoner;
      data.monsters = monsters;
      data.secret = secret;
    }
    steem.broadcast.customJson(KEYS.posting, [], [KEYS.username], "sm_submit_team", JSON.stringify(data), async (err, result) => {
      if (err) throw err;
      console.log("Broadcasted sm_submit_team");
      this.findMatchId = result.id;
      if (!skipReveal) {
        await new Promise(resolve => setTimeout(resolve, 3300));
        console.log("Revealing team...");
        steem.broadcast.customJson(KEYS.posting, [], [KEYS.username], "sm_team_reveal", JSON.stringify({
          ...data,
          summoner: summoner,
          monsters: monsters,
          secret: secret
        }), (err, result) => {
          console.log("Revealed team!");
        });
      }
    });
  }
  _revealTeam() {

  }
  async _checkBattleStatus() {
    if (!this.findMatchId) return;
    const rawResponse = await fetch("https://api.steemmonsters.io/battle/status?id=" + this.findMatchId);
    const json = await rawResponse.json();
    this.status.data = json;

    if ((typeof json) === "string") {
      console.log(json);
      this.status.statusName = "battleTxProcessing";
      this.callback(this.status);
      return;
    }

    if (json.error) {
      this.status.statusName = "error";
    } else if (json.status === 0) {
      this.status.statusName = "searchingForEnemy";
    } else if (json.status === 1) {
      this.status.statusName = "enemyFound";
    } else if (json.status === 3) {
      this.status.statusName = "noEnemyFound";
    }
    this.callback(this.status);
  }
  _checkBattleTrxStatus() {

  }
  static generatePassword(length = 10) {
    var charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    retVal = "";
    for (var i = 0, n = charset.length; i < length; ++i) {
      retVal += charset.charAt(Math.floor(Math.random() * n));
    }
    return retVal;
  }
}
async function getSMJson(url) {
  const res = await (fetch("https://api.steemmonsters.io" + url));
  const text = await res.text();
  try {
    return JSON.parse(text);
  } catch (e) {
    console.log("Invalid JSON; retrying", text)
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return await getSMJson();
  }
}

async function main() {
  let curBlock = -1;
  steem.api.streamBlockNumber((err, b) => curBlock = b);
  let ourCollection = (await getSMJson("/cards/collection/" + KEYS.username)).cards;
  setInterval(async () => { ourCollection = (await getSMJson("/cards/collection/" + KEYS.username)).cards; scanCollection(); }, 1200000);
  function scanCollection() {
    ourCollection = ourCollection.filter(card => canPlayCard(card));
  }
  scanCollection();
  setInterval(() => scanCollection(), 25000);
  function bestCard(id) {
    return ourCollection.filter(card => (card.card_detail_id === id))
      .map(card => ({...card, rarity: cardData.filter(cardD => card.card_detail_id === cardD.id)[0].rarity}))
      .sort((a, b) => { console.log(a,b); return cardBcx(a.xp, a.rarity, a.edition, a.gold) - cardBcx(b.xp, b.rarity, b.edition, b.gold) }).reverse()[0];
  }
  function canPlayCard(card) {
    if (card.market_id)
      return false;
    if (!card.last_transferred_block || !card.last_used_block)
      return true;

    if (curBlock === -1) return true;
    var last_block = curBlock;
    return card.last_transferred_block <= last_block - 201600 || card.last_used_block <= last_block - 201600;
  }
  var submittedTeam = false;
  const battle = new Battle(async status => {
    console.log(status.statusName);
    if (!submittedTeam && (status.statusName === "enemyFound")) {
      var mana = status.data.mana_cap;
       var manaUsed = 5; //for summoner
  let cardsToScore = [23,28,32,33].filter(id => possibleCards(battle, "Green").map(a => a.id).indexOf(id) > -1)
        cardsToScore = cardsToScore.map(ele => cardData.filter(card => card.id === ele)[0])
    let team = []; // will contain the cards that fit under the mana cap soon
    var nonRangedUsed = 0;
    for (let i = 0; i < cardsToScore.length; i++) {
      const card = cardsToScore[i];
      const cardMana = card.stats.mana[0] ? card.stats.mana[0] : card.stats.mana;
      //verify it's in our collection
      if (ourCollection.filter(colCard => card.id === colCard.card_detail_id)[0] === undefined) continue;
      if ((manaUsed + cardMana) > battle.mana_cap) {
        if (team.length < 6) continue;
        let lastCardMana = team[team.length - 1].stats.mana[0] ? team[team.length - 1].stats.mana[0] : team[team.length - 1].stats.mana;
        if (((manaUsed - lastCardMana + cardMana) <= battle.mana_cap) && (cardMana > lastCardMana)) {
          team[team.length - 1] = card;
        } else {
          continue;
        }
      } else if (team.length < 6) {
        if (card.stats.ranged[0] === 0) {
         //not a ranged monster
          if (card.id !== 91) nonRangedUsed++; //ignore ooze
        } else if ((nonRangedUsed < 2) && (team.length > 4)) {
          //Ranged monster, and we have more than 4 monsters already. We need more melee monsters now, as we have either only 0 or 1, so skip this
          continue;
        }
        team.push(card);
      }
      manaUsed += cardMana;
    }

      battle.broadcastTeam(bestCard(112).uid,team.map(card => bestCard(card.id).uid));
      submittedTeam = true;
    }
  });
}
main();
